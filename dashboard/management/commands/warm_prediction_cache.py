from django.core.management.base import BaseCommand
from dashboard.tasks import prewarm_prediction_cache
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Pre-warm the prediction cache for faster API responses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Run synchronously instead of as a Celery task',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all prediction caches before warming',
        )

    def handle(self, *args, **options):
        sync = options['sync']
        clear_cache = options['clear']

        if clear_cache:
            self.stdout.write('Clearing existing prediction caches...')
            # Clear prepared data
            cache.delete('prepared_sugar_data')
            
            # Clear all prediction caches
            for days in [7, 14, 30]:
                for model in ['auto', 'arima', 'ets', 'ma']:
                    for ci in ['True', 'False']:
                        cache_key = f'prediction_api_{days}_{model}_{ci}'
                        cache.delete(cache_key)
            
            self.stdout.write(self.style.SUCCESS('✓ Caches cleared'))

        self.stdout.write('Warming prediction cache...')
        
        if sync:
            # Run synchronously
            result = prewarm_prediction_cache()
            
            if result.get('status') == 'success':
                self.stdout.write(self.style.SUCCESS('\n✓ Cache warming completed successfully'))
                self.stdout.write('\nCached predictions:')
                for period, status in result.get('results', {}).items():
                    self.stdout.write(f'  {period}: {status}')
            else:
                self.stdout.write(self.style.ERROR(f'\n✗ Cache warming failed: {result.get("error")}'))
        else:
            # Run as Celery task
            task = prewarm_prediction_cache.delay()
            self.stdout.write(self.style.SUCCESS(f'\n✓ Cache warming task queued: {task.id}'))
            self.stdout.write('Use --sync flag to run synchronously and see immediate results')